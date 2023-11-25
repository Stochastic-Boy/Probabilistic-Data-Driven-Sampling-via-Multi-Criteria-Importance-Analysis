library(ggplot2)

BROWN <- "#AD8C97"
BROWN_DARKER <- "#7d3a46"
GREEN <- "#2FC1D3"
BLUE <- "#076FA1"
GREY <- "#C7C9CB"
GREY_DARKER <- "#5C5B5D"
RED <- "#E3120B"


srs <- as.data.frame(read.csv("srs_time.csv", header = F))
colnames(srs) <- c("Processes","Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
srs_new <- as.matrix(srs[order(srs$Sampling_Ratio, decreasing = F), ])
srs_reduced <- matrix(0, ncol = 8, nrow = 70)

for(i in 1:70)
{
  temp <- rep(0,6)
  for(j in 1:10)
  {
    temp = temp + as.vector(srs_new[10*(i-1)+j,3:8])
  }
  srs_reduced[i,] = c(srs_new[10*(i-1)+1,1],srs_new[10*(i-1)+1,2],temp/10)
}

colnames(srs_reduced) <- c("Processes","Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
srs_reduced = as.data.frame(srs_reduced)
srs_reduced$Sampling_Ratio = factor(as.numeric(srs_reduced$Sampling_Ratio ))


plt1 <- ggplot(srs_reduced, aes(x = Processes, y = total_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt1

plt8 <- ggplot(srs_reduced, aes(x = Processes, y = Reading_time+saving_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt8



plt9 <- ggplot(srs_reduced, aes(x = Processes, y = comp_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt9

plt9 <- ggplot(srs_reduced, aes(x = Processes, y = scatter_time+ gather_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt9


srs_reduced <- srs_reduced[order(srs_reduced$Processes, decreasing = F), ]
srs_reduced = as.matrix(srs_reduced)
srs_reduced = as.data.frame(srs_reduced)
srs_reduced$Processes = factor(as.numeric(srs_reduced$Processes ))
plt2 <- ggplot(srs_reduced, aes(x = Sampling_Ratio, y = total_time, group = Processes)) +
  geom_line(aes(color = Processes), linewidth = 1) +
  geom_point(
    aes(fill = Processes), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"orange")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"orange")) + 
  scale_y_discrete(breaks = seq(1,90,by = 15)) + theme(legend.position = "bottom")

plt2


library(dplyr)
vbs <- as.data.frame(read.csv("vbs_time.csv"),header=F)
colnames(vbs) <-  c("Processes","Bins", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
vbs_time_node <- filter(vbs, vbs$Bins == 16)
vbs_time_node <- as.matrix(vbs_time_node[order(vbs_time_node$Sampling_Ratio), ])
curr = 1
j=1
vbs_red_16 <- matrix(0,ncol = 8,nrow = 19)
for(i in 1:19)
{
  temp = rep(0,6)
  k=0
  while(j<=87 && vbs_time_node[j,1] == curr)
  {
    temp = temp + vbs_time_node[j, 4:9]
    j=j+1
    k=k+1
  }
  vbs_red_16[i, ] = c(vbs_time_node[j-1,1],vbs_time_node[j-1,3],temp/k)
  curr = 2*curr
  if(curr == 128){curr = 1}
}
colnames(vbs_red_16) = c("Processes", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")

vbs_red_16 = as.data.frame(vbs_red_16)
vbs_red_16 = vbs_red_16[-(15:19), ]
vbs_red_16$Sampling_Ratio = factor(vbs_red_16$Sampling_Ratio )


plt3 <- ggplot(vbs_red_16, aes(x = Processes, y = total_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt3

plt10 <- ggplot(vbs_red_16, aes(x = Processes, y = Reading_time+saving_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt10

plt11 <- ggplot(vbs_red_16, aes(x = Processes, y = scatter_time+gather_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt11


plt12 <- ggplot(vbs_red_16, aes(x = Processes, y = comp_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt12

vbs <- as.data.frame(read.csv("vbs_time.csv"),header=F)
colnames(vbs) <-  c("Processes","Bins", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
vbs_time_node <- filter(vbs, vbs$Bins == 16)
vbs_time_node <- as.matrix(vbs_time_node[order(vbs_time_node$Sampling_Ratio), ])
curr = 1
j=1
vbs_red_16 <- matrix(0,ncol = 8,nrow = 19)
for(i in 1:19)
{
  temp = rep(0,6)
  k=0
  while(j<=87 && vbs_time_node[j,1] == curr)
  {
    temp = temp + vbs_time_node[j, 4:9]
    j=j+1
    k=k+1
  }
  vbs_red_16[i, ] = c(vbs_time_node[j-1,1],vbs_time_node[j-1,3],temp/k)
  curr = 2*curr
  if(curr == 128){curr = 1}
}
colnames(vbs_red_16) = c("Processes", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")

vbs_red_16 = as.data.frame(vbs_red_16)
vbs_red_16 <- vbs_red_16[order(vbs_red_16$Processes, decreasing = F), ]
vbs_red_16 = as.matrix(vbs_red_16)
vbs_red_16 = as.data.frame(vbs_red_16)
vbs_red_16$Processes = factor(as.numeric(vbs_red_16$Processes ))
plt4 <- ggplot(vbs_red_16, aes(x = Sampling_Ratio, y = total_time, group = Processes)) +
  geom_line(aes(color = Processes), linewidth = 1) +
  geom_point(
    aes(fill = Processes), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"orange")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"orange")) + 
  scale_y_discrete(breaks = seq(1,90,by = 15)) + theme(legend.position = "bottom")

plt4


vbs <- as.data.frame(read.csv("vbs_time.csv"),header=F)
colnames(vbs) <-  c("Processes","Bins", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
vbs_samp_01 = filter(vbs,vbs$Sampling_Ratio== 0.001)
vbs_samp_01 = as.matrix(vbs_samp_01)
## vbs_samp_01 <- as.matrix(vbs_samp_01[order(vbs_time_node[,2]), ])
curr = 1
j=1
vbs_time_bin <- matrix(0,ncol = 8,nrow = 42)
for(i in 1:42)
{
  temp = rep(0,6)
  k=0
  while(j<=180 && vbs_samp_01[j,2] == curr)
  {
    temp = temp + vbs_samp_01[j, 4:9]
    j=j+1
    k=k+1
  }
  vbs_time_bin[i, ] = c(vbs_samp_01[j-1,1],vbs_samp_01[j-1,2],temp/k)
  curr = 2*curr
  if(curr == 64){curr = 1}
}
vbs_time_bin = vbs_time_bin[c(-36,-42), ]
colnames(vbs_time_bin) = c("Processes", "Bins","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
vbs_time_bin <- as.data.frame(vbs_time_bin)
vbs_time_bin$Processes <- factor(vbs_time_bin$Processes)

plt5 <- ggplot(vbs_time_bin, aes(x = Bins, y = total_time, group = Processes)) +
  geom_line(aes(color = Processes), linewidth = 1) +
  geom_point(
    aes(fill = Processes),
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY, "orange")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"orange")) +
 # Do not include any legend
  theme(legend.position = "bottom")

plt5



gbs <- as.data.frame(read.csv("gbs_time.csv",header = F))
colnames(gbs) <-  c("Processes","Bins", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
gbs_time_node <- as.matrix(filter(gbs, gbs$Bins == 16))
j=1

gbs_red_16 <- matrix(0,ncol = 8,nrow = 7)
for(i in 1:7)
{
  temp = rep(0,6)
  for(k in c(1,2,3))
  {
    temp = temp + as.vector(as.numeric(gbs_time_node[j, 4:9]))
    j=j+1
  }
  gbs_red_16[i, ] = c(gbs_time_node[j-1,1],gbs_time_node[j-1,3],temp/3)
}
colnames(gbs_red_16) = c("Processes", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")

gbs_red_16 = as.data.frame(gbs_red_16)
gbs_red_16$Sampling_Ratio = factor(as.numeric(gbs_red_16$Sampling_Ratio ))


plt6 <- ggplot(gbs_red_16, aes(x = Processes, y = total_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt6


plt13 <- ggplot(gbs_red_16, aes(x = Processes, y = gather_time+scatter_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt13


plt14 <- ggplot(gbs_red_16, aes(x = Processes, y = comp_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt14

plt14 <- ggplot(gbs_red_16, aes(x = Processes, y = Reading_time+saving_time), group = Sampling_Ratio) +
  geom_line(aes(color = Sampling_Ratio), linewidth = 1) +
  geom_point(
    aes(fill = Sampling_Ratio), 
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"yellow", "orange","plum","cyan")) +
  scale_x_log10()+
  # Do not include any legend
  theme(legend.position = "bottom")

plt14


gbs <- as.data.frame(read.csv("gbs_time.csv",header=F))
colnames(gbs) <-  c("Processes","Bins", "Sampling_Ratio","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
gbs_samp_01 = filter(gbs,gbs$Sampling_Ratio== 0.01)
gbs_samp_01 = as.matrix(gbs_samp_01)
j=1
gbs_time_bin <- matrix(0,ncol = 8,nrow = 35)
for(i in 1:35)
{
  temp = rep(0,6)
  for(k in c(1,2,3))
  {
    temp = temp + as.vector(gbs_samp_01[j, 4:9])
    j=j+1
  }
  gbs_time_bin[i, ] = c(gbs_samp_01[3*(i-1)+1,1],gbs_samp_01[3*(i-1)+1,2],temp/3)
}

colnames(gbs_time_bin) = c("Processes", "Bins","Reading_time","scatter_time","comp_time","gather_time","saving_time","total_time")
gbs_time_bin <- as.data.frame(gbs_time_bin)
gbs_time_bin$Processes <- factor(gbs_time_bin$Processes)

plt7 <- ggplot(gbs_time_bin, aes(x = Bins, y = total_time, group = Processes)) +
  geom_line(aes(color = Processes), linewidth = 1) +
  geom_point(
    aes(fill = Processes),
    size = 3, 
    pch = 21, # Type of point that allows us to have both color (border) and fill.
    color = "white", 
    stroke = 1 # The width of the border, i.e. stroke.
  ) + scale_color_manual(values = c(BLUE, GREEN, BROWN,BROWN_DARKER,RED,GREY, "orange")) +
  scale_fill_manual(values = c(BLUE, GREEN, BROWN, BROWN,BROWN_DARKER,RED,GREY,"orange")) +
  # Do not include any legend
  theme(legend.position = "bottom")

plt7